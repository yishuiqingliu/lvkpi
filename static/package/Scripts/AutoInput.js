; (function ($, window, document, undefined) {

  $.fn.autoinput = function (source, parameters) {
    var
      $allModules = $(this),
      moduleSelector = $allModules.selector || '',
      time = new Date().getTime(),
      performance = [],
      query = arguments[0],
      methodInvoked = (typeof query == 'string'),
      queryArguments = [].slice.call(arguments, 1),
      returnedValue
    ;

    $(this)
      .each(function () {
        var
          settings = $.extend(true, {}, $.fn.autoinput.settings, parameters),
          className = settings.className,
          selector = settings.selector,
          error = settings.error,
          namespace = settings.namespace,

          eventNamespace = '.' + namespace,
          moduleNamespace = namespace + '-module',

          $module = $(this),
          $auto = $module.find(selector.auto),
          $results = $module.find(selector.results),
          $result = $module.find(selector.result),

          element = this,
          instance = $module.data(moduleNamespace),

          module
        ;
        module = {
          initialize: function () {
            module.verbose('Initializing module');
            var
              inputEvent = module.get.changeEvent();
            ;
            $auto
              .on('focus' + eventNamespace, module.event.focus)
              .on('blur' + eventNamespace, module.event.blur)
              .on('keydown' + eventNamespace, module.handleKeyboard)
              .on(inputEvent + eventNamespace, module.complete.throttle)
            ;
            $results
              .on('click' + eventNamespace, selector.result, module.results.select)
            ;
            module.instantiate();
          },

          instantiate: function () {
            module.verbose('Storing instance of module', module);
            instance = module;
            $module
              .data(moduleNamespace, module)
            ;
          },
          destroy: function () {
            module.verbose('Destroying instance');
            $module
              .removeData(moduleNamespace)
            ;
          },
          event: {
            focus: function () {
              $module
                .addClass(className.focus)
              ;
              module.results.show();
            },
            blur: function () {
              $module
                .removeClass(className.focus)
              ;
              module.results.hide();
            }
          },
          handleKeyboard: function (event) {
            var
              $result = $module.find(selector.result),
              keyCode = event.which,
              keys = {
                backspace: 8,
                enter: 13,
                escape: 27,
                upArrow: 38,
                downArrow: 40
              },
              activeClass = className.active,
              currentIndex = $result.index($result.filter('.' + activeClass)),
              resultSize = $result.size(),
              newIndex
            ;

            if ($result.filter(':visible').size() > 0) {
              if (keyCode == keys.enter) {
                module.verbose('Enter key pressed, selecting active result');
                if ($result.filter('.' + activeClass).exist()) {
                  $.proxy(module.results.select, $result.filter('.' + activeClass))();
                  event.preventDefault();
                  return false;
                }
              }
              else if (keyCode == keys.upArrow) {
                module.verbose('Up key pressed, change active result');
                newIndex = (currentIndex - 1 < 0)
                  ? currentIndex
                  : currentIndex - 1
                ;
                $result
                  .removeClass(activeClass)
                  .eq(newIndex)
                    .addClass(activeClass)
                ;
                event.preventDefault();
              }
              else if (keyCode == keys.downArrow) {
                module.verbose('Down key pressed, change active result');
                newIndex = (currentIndex + 1 >= resultSize)
                  ? currentIndex
                  : currentIndex + 1
                ;
                $result
                  .removeClass(activeClass)
                  .eq(newIndex)
                    .addClass(activeClass)
                ;
                event.preventDefault();
              }
            }
          },
          complete: {
            cancel: function () {
              var
                xhr = $module.data('xhr') || false
              ;
              if (xhr && xhr.state() != 'resolved') {
                module.debug('Cancelling last search');
                xhr.abort();
              }
            },
            throttle: function () {
              var
                searchTerm = $auto.val(),
                numCharacters = searchTerm.length
              ;
              clearTimeout(module.timer);
              if (numCharacters >= settings.minCharacters) {
                module.timer = setTimeout(module.complete.query, settings.searchThrottle);
              }
              else {
                module.results.hide();
              }
            },
            query: function () {
              var
                searchTerm = $auto.val(),
                cachedHtml = module.complete.cache.read(searchTerm)
              ;
              if (cachedHtml) {
                module.debug('Read result for "' + searchTerm + '" from cache');
                module.results.add(cachedHtml);
              }
              else {
                module.debug('Querying for "' + searchTerm + '"');
                if (typeof source == 'object') {
                  module.complete.local(searchTerm);
                }
                else {
                  module.complete.remote(searchTerm);
                }
                $.proxy(settings.onSearchQuery, $module)(searchTerm);
              }
            },
            local: function (searchTerm) {
              var
                results = [],
                fullTextResults = [],
                searchRegExp = new RegExp('(?:\s|^)' + searchTerm, 'i'),
                searchHtml
              ;
              $module
                .addClass(className.loading)
              ;
              $.each(source, function (label, thing) {
                if (searchRegExp.test(thing)) {
                  results.push(thing);
                }
              });
              searchHtml = module.results.generate(results);
              $module
                .removeClass(className.loading)
              ;
              module.complete.cache.write(searchTerm, searchHtml);
              module.results.add(searchHtml);
            },
            remote: function (searchTerm) {
              var
                apiSettings = {
                  stateContext: $module,
                  url: source,
                  urlData: { query: searchTerm },
                  success: function (response) {
                    searchHtml = module.results.generate(response);
                    module.complete.cache.write(searchTerm, searchHtml);
                    module.results.add(searchHtml);
                  },
                  failure: module.error
                },
                searchHtml
              ;
              module.complete.cancel();
              module.debug('Evecuting search');
              $.extend(true, apiSettings, settings.apiSettings);
              $.api(apiSettings);
            },
            cache: {
              read: function (name) {
                var
                  cache = $module.data('cache')
                ;
                return (settings.cache && (typeof cache == 'object') && (cache[name] !== undefined))
                  ? cache[name]
                  : false
                ;
              },
              write: function (name, value) {
                var
                  cache = ($module.data('cache') !== undefined)
                    ? $module.data('cache')
                    : {}
                ;
                cache[name] = value;
                $module
                  .data('cache', cache)
                ;
              }
            }
          },
          results: {
            generate: function (results) {
              module.debug('Generating html form source', results);
              var
                template = settings.templates.message,
                html = ''
              ;
              if ($.isPlainObject(results) && (!$.isEmptyObject(results)) || ($.isArray(results) && results.length > 0)) {
                if (settings.maxResults > 0) {
                  results = $.makeArray(results).slice(0, settings.maxResults);
                }
                if (results.length > 0) {
                  if ($.isFunction(template)) {
                    html = template(results);
                  }
                  else {
                    module.error(error.noTemplate, false);
                  }
                }
              }
              else {
                html = module.message(error.noResults, 'empty');
              }
              $.proxy(settings.onResults, $module)(results);
              return html;
            },
            add: function (html) {
              $results
                .html(html)
              ;
              module.results.show();
            },
            show: function () {
              if (($result.filter(':visible').size() === 0)
                  && ($auto.filter(':focus').size() > 0)
                  && $results.html() !== '') {
                $results
                  .stop()
                  .fadeIn(200)
                ;
                $.proxy(settings.onResultsOpen, $results)();
              }
            },
            hide: function () {
              if ($results.filter(':visible').size() > 0) {
                $results
                  .stop()
                  .fadeOut(200)
                ;
                $.proxy(settings.onResultClose, $results)();
              }
            },
            select: function () {
              module.debug('Search result selected');
              var
                $result = $(this),
                $title = $result.find('.title'),
                title = $title.html()
              ;
              module.results.hide();
              $auto
                .val(title)
              ;
              $.proxy(settings.onResultSelect, $module)(title);
            }
          },

          get: {
            changeEvent: function() {
              return (document.createElement('input').oninput !== undefined)
                ? 'input'
                : (document.createElement('input').onpropertychange !== undefined)
                  ? 'propertychange'
                  : 'keyup'
              ;
            }
          },
          debug: function () {
            if (settings.debug) {
              if (settings.performance) {
                module.performance.log(arguments);
              }
              else {
                module.debug = Function.prototype.bind.call(console.info, console, settings.name + ':');
                module.debug.apply(console, arguments);
              }
            }
          },
          verbose: function () {
            if (settings.verbose && settings.debug) {
              if (settings.performance) {
                module.performance.log(arguments);
              }
              else {
                module.verbose = Function.prototype.bind.call(console.info, console, settings.name + ':');
                module.verbose.apply(console, arguments);
              }
            }
          },
          error: function () {
            module.error = Function.prototype.bind.call(console.info, console, settings.name + ':');
            module.error.apply(console, arguments);
          },
          performance: {
            log: function (message) {
              var
                currentTime,
                executionTime,
                previousTime
              ;
              if (settings.performance) {
                currentTime = new Date().getTime();
                previousTime = time || currentTime;
                executionTime = currentTime - previousTime;
                time = currentTime;
                performance.push({
                  'Element': element,
                  'Name': message[0],
                  'Argument': [].slice.call(message, 1) || '',
                  'Execution Time': executionTime
                });
              }
              clearTimeout(module.performance.timer);
              module.performance.timer = setTimeout(module.performance.display, 100);
            },
            display: function () {
              var
                title = settings.name + ':',
                totalTime = 0
              ;
              time = false;
              clearTimeout(module.performance.timer);
              $.each(performance, function (index, data) {
                totalTime += data['Execution Time'];
              });
              title += ' ' + totalTime + 'ms';
              if (moduleSelector) {
                title += ' \'' + moduleSelector + '\'';
              }
              if ((console.group !== undefined || console.table !== undefined) && performance.length > 0) {
                console.groupCollapsed(title);
                if (console.table) {
                  console.table(performance);
                }
                else {
                  $.each(performance, function (index, data) {
                    console.log(data['Name'] + ':' + data['Execution Time'] + 'ms');
                  });
                }
                console.groupEnd();
              }
              performance = [];
            }
          },
          invoke: function (query, passedArguments, context) {
            var
              maxDepth,
              found,
              response
            ;
            passedArguments = passedArguments || queryArguments;
            context = element || context;
            if (typeof query == 'string' && instance !== undefined) {
              query = query.split(/[]. ]/);
              maxDepth = query.length - 1;
              $.each(query, function (depth, value) {
                var camelCaseValue = (depth != maxDepth)
                  ? value + query[depth + 1].charAt(0).toUpperCase() + query[depth + 1].slice(1)
                  : query
                ;
                if ($.isPlainObject(instance[value]) && (depth != maxDepth)) {
                  instance = instance[value];
                }
                else if ($.isPlainObject(instance[camelCaseValue]) && (depth != maxDepth)) {
                  instance = instance[camelCaseValue];
                }
                else if (instance[value] !== undefined) {
                  found = instance[value];
                  return false;
                }
                else if (instance[camelCaseValue] !== undefined) {
                  found = instance[camelCaseValue];
                  return false;
                }
                else {
                  module.error(error.method);
                  return false;
                }
              });
            }
            if ($.isFunction(found)) {
              response = found.apply(context, passedArguments);
            }
            else if (found !== undefined) {
              response = found;
            }
            if ($.isArray(returnedValue)) {
              returnedValue.push(response);
            }
            else if (typeof returnedValue == 'string') {
              returnedValue = [returnedValue, response];
            }
            else if (response !== undefined) {
              returnedValue = response;
            }
            return found;
          }
        };
        if (methodInvoked) {
          if (instance === undefined) {
            module.initialize();
          }
          module.invoke(query);
        }
        else {
          if (instance !== undefined) {
            module.destroy();
          }
          module.initialize();
        }
      })
    ;

    return (returnedValue !== undefined)
      ? returnedValue
      : this
    ;
  };

  $.fn.autoinput.settings = {
    name: 'Auto complete input',
    namespace: 'autoinput',
    debug: true,
    verbose: true,
    performance: true,

    onResultSelect: function (result) {},
    onResults: function (results) { },
    onSearchQuery: function () { },
    onResultsOpen: function () { },
    onResultClose: function () { },
    automatic: 'true',
    type: 'simple',

    minCharacters: 0,
    searchThrottle: 300,
    maxResults: 5,
    cache: true,

    apiSettings: {
    },

    className: {
      active: 'active',
      focus: 'focus',
      loading: 'loading'
    },

    error: {
      method: 'The method you called is not defined.',
      noResults: 'No match results exist.'
    },

    selector: {
      auto: '.autocomplete',
      results: '.results',
      result: '.result'
    },

    templates: {
      message: function (results) {
        var
          html = ''
        ;
        if (results !== undefined) {
          //html += '<div class="description">' + message + '</div>';
          $.each(results, function (index, result) {
            html += '<div class="result"><div class="title">' + result + "</div></div>";
          })
        }
        return html;
      }
    }
  };

})(jQuery, window, document);