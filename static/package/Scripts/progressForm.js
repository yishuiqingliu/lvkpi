; (function ($, window, document, undefined) {
  $.fn.progressform = function (parameters) {
    var
      settings = $.extend(true, {}, $.fn.progressform.settings, parameters),
      $module = $(this),
      $field = $(this).find(settings.selector.field),
      $group = $(this).find(settings.selector.group),
      $tabs = $(this).find(settings.selector.tabs),
      $steps = $(this).find(settings.selector.steps),
      $buttons = $tabs.find(settings.selector.buttons).not(settings.selector.submits),
      $submit = $(this).find(settings.selector.submit),
      $form = $(settings.selector.form),
      $formatInput = $(settings.selector.input).filter("[" + settings.metadata.format + "]"),

      moduleSelector = $module.selector || '',

      activeTabPath,

      element = this,
      time = new Date().getTime(),
      performance = [],

      className = settings.className,
      metadata = settings.metadata,
      error = settings.error,

      eventNamespace = '.' + settings.namespace,
      moduleNamespace = settings.namespace + '-module',

      instance = $module.data(moduleNamespace),
      query = arguments[0],
      methodInvoked = (instance !== undefined && typeof query == 'string'),
      queryArguments = [].slice.call(arguments, 1),

      module,
      invokedResponse
    ;

    module = {
      initialize: function () {
        if (!$.isWindow(element)) {
          $steps
            .on('click' + eventNamespace, module.event.stepClick)
          ;
          $buttons
            .on('click' + eventNamespace, module.event.next)
          ;
          $field
            .on(module.get.changeEvent() + eventNamespace, module.event.field.change)
          ;
          $submit
            .on('click' + eventNamespace, module.event.submit)
          ;
          if (settings.keyboardShortcuts) {
            $field
              .on('keydown' + eventNamespace, module.event.field.keydown)
            ;
          }
          if (settings.formatInput) {
            $formatInput
              .on(module.get.changeEvent() + eventNamespace, module.event.field.format)
            ;
          }
        }
        module.instantiate();
      },

      instantiate: function () {
        module.verbose('Storeing instance of module', module);
        $module
          .data(moduleNamespace, module)
        ;
      },

      destroy: function () {
        module.debug('Destroying progressform', $module);
        $module
          .off(eventNamespace)
        ;
      },

      event: {
        next: function () {
          module.debug('Next clicked');
          var
            tab = $(this).parents(settings.selector.tabs),
            currnetTabPath = tab.data(metadata.tab),
            nextTabPath = tab.next().data(metadata.tab)
          ;

          if (nextTabPath !== undefined) {
            if (module.validate.tab(currnetTabPath)) {
              module.changeStep(nextTabPath);
            } else {
              module.debug('Tab does not finished');
            }
          } else {
            module.debug('No next step');
          }
        },
        stepClick: function () {
          module.debug('Step clicked');
          var
            tabPath = $(this).data(metadata.tab),
            disable = $(this).hasClass(className.disabled)
          ;
          if (disable) {
            module.debug('Click disable step');
            return;
          }
          if (tabPath !== undefined) {
            module.changeStep(tabPath);
          } else {
            module.debug('No step specified');
          }
        },
        submit: function () {
          module.verbose('Submitting form', $module);
          var
            tabPath = $(this).parents(settings.selector.tabs).data(metadata.tab)
          ;
          if (tabPath !== undefined) {
            if (module.validate.tab(tabPath)) {
              $form
                .submit()
              ;
            } else {
              module.debug('Tab does not finished');
            }
          } else {
            module.debug('No next step');
          }
        },
        field: {
          change: function () {
            var
              $field = $(this),
              $fieldGroup = $field.closest($group)
            ;
            if ($fieldGroup.hasClass(className.error)) {
              module.debug('Revalidating field', $field);
              module.validate.field(this);
            }
          },
          keydown: function (event) {
            var
              $field = $(this),
              key = event.which,
              keyCode = {
                enter: 13,
                escape: 27
              }
            ;
            if (key == keyCode.escape) {
              module.verbose('Escape key pressed blurring field');
              $field.blur();
            }
            if (!event.ctrlKey && key == keyCode.enter) {
              module.debug('Enter key pressed, submitting form');
              $field
                  .one('keyup' + eventNamespace, module.event.field.keyup)
              ;
              event.preventDefault();
              return false;
            }
          },
          keyup: function () {
            var
              tab = $(this).parents(settings.selector.tabs)
            ;
            module.verbose('Doing keybord shortcut from click button');
            $(tab).find(settings.selector.buttons).click();
          },
          format: function () {
            var
              formatType = $(this).attr('')
            ;
          }
        }
      },

      refresh: function () {
        module.verbose('Refreshing progress');
      },

      changeStep: function (tabPath) {
        module.deactivate.all();
        var
          isTab = module.is.tab(tabPath),
          $tab = module.get.tabElement(tabPath)
        ;
        module.verbose('Looking for tab', tabPath);
        if (isTab) {
          module.verbose('Tab was found', tabPath);
          activeTabPath = tabPath;
          module.debug('Opened local tab', tabPath);
          module.activate.all(tabPath);
        }
      },

      validate: {
        tab: function (tabPath) {
          var
            $tab = module.get.tabElement(tabPath),
            $fields = $tab.find(settings.selector.field),
            allValid = true
          ;
          $.each($fields, function (index, field) {
            if (!module.validate.field(field)) {
              allValid = false;
            }
          });
          return allValid;
        },

        field: function (field) {
          var
              $field = $(field),
              $fieldGroup = $field.closest($group),
              value = $field.val()
          ;
          if (value === undefined || '' === value) {
            $fieldGroup.addClass(className.error);
            return false;
          } else {
            $fieldGroup.removeClass(className.error);
            return true;
          }
        }
      },

      formatInput: {
        digit: function (distance) {
          var
            value = $(this).value(),
            formatRegex = new RegExp("\\B(?=(\\d{" + distance.toString() + "})+(?!\\d))", "g"),
            digitValue = value.toString().replace(/ /g, ''),
            formatValue = digitValue.replace(formatRegex, " ").trim()
          ;
          return formatValue;
        }
      },

      activate: {
        all: function (tabPath) {
          module.activate.tab(tabPath);
          module.activate.step(tabPath);
        },
        tab: function (tabPath) {
          var
            $tab = module.get.tabElement(tabPath)
          ;
          module.verbose('Showing tab content for', $tab);
          $tab.addClass(className.active);
        },
        step: function (tabPath) {
          var
            $step = module.get.stepElement(tabPath)
          ;
          module.verbose('Active step for', $step);
          $step.removeClass(className.disabled);
          $step.addClass(className.active);
        }
      },
      deactivate: {
        all: function () {
          module.deactivate.steps();
          module.deactivate.tabs();
        },
        steps: function () {
          $steps.removeClass(className.active);
        },
        tabs: function () {
          $tabs.removeClass(className.active);
        }
      },
      is: {
        tab: function (tabName) {
          return (tabName !== undefined)
            ? (module.get.tabElement(tabName).size() > 0)
            : false
          ;
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
        },
        tabElement: function (tabPath) {
          tabPath = tabPath || activeTabPath;
          return $tabs.filter('[data-' + metadata.tab + '="' + tabPath + '"]');
        },
        stepElement: function (tabPath) {
          tabPath = tabPath || activeTabPath;
          return $steps.filter('[data-' + metadata.tab + '="' + tabPath + '"]');
        },
        tab: function () {
          return activeTabPath;
        }
      },

      setting: function (name, value) {
        if (value !== undefined) {
          if ($.isPlainObject(name)) {
            $.extend(true, settings, name);
          }
          else {
            settings[name] = value;
          }
        }
        else {
          return settings[name];
        }
      },
      internal: function (name, value) {
        if (value !== undefined) {
          if ($.isPlainObject(name)) {
            $.extend(true, module, name);
          }
          else {
            module[name] = value;
          }
        }
        else {
          return module[name];
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
        if ($.isArray(invokedResponse)) {
          invokedResponse.push(response);
        }
        else if (typeof invokedResponse == 'string') {
          invokedResponse = [invokedResponse, response];
        }
        else if (response !== undefined) {
          invokedResponse = response;
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
    return (invokedResponse !== undefined)
      ? invokedResponse
      : this
    ;
  };

  $.progressform = function (settings) {
    $(window).tab(settings);
  };

  $.fn.progressform.settings = {
    name: 'progressform',
    verbose: true,
    debug: true,
    performance: true,
    namespace: 'progressform',
    keyboardShortcuts: true,
    formatInput: true,

    context: 'body',

    error: {
      api: 'You attempted to load content without API module',
      method: 'The method you called is not defined',
      state: 'The state library has not been initialized',
    },

    metadata: {
      tab: 'tab',
      format: 'format'
    },

    className: {
      disabled: 'disabled',
      active: 'active',
      error: 'error'
    },

    selector: {
      tabs: '.tab',
      steps: '.step',
      buttons: '.button',
      field: 'input, textarea, select',
      group: '.field',
      submit: '.submit',
      form: 'form',
      input: 'input'
    },

    rules: {
      empty: function (value) {
        return !(value === undefined || '' === value);
      },
      price: function (value) {
        var
          priceRegExp = new RegExp("^[0-9]+(\.[0-9]{1,2})?$")
        ;
        return priceRegExp.test(value);
      }
    }
  };
})(jQuery, window, document);