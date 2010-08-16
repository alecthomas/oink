// Originally from http://ejohn.org/blog/simple-javascript-inheritance/
// Inspired by base2 and Prototype
(function(){
  var initializing = false, fnTest = /xyz/.test(function(){xyz;}) ? /\b_super\b/ : /.*/;
  //
  // Top-level namespace
  this.Oink = {};

  // The base Class implementation (does nothing)
  Oink.Class = function(){};
  
  // Create a new Class that inherits from this class
  Oink.Class.extend = function(prop) {
    var _super = this.prototype;
    
    // Instantiate a base class (but only create the instance,
    // don't run the __init__ constructor)
    initializing = true;
    var prototype = new this();
    initializing = false;
    
    // Copy the properties over onto the new prototype
    for (var name in prop) {
      // Check if we're overwriting an existing function
      prototype[name] = typeof prop[name] == "function" && 
        typeof _super[name] == "function" && fnTest.test(prop[name]) ?
        (function(name, fn){
          return function() {
            var tmp = this._super;
            
            // Add a new ._super() method that is the same method
            // but on the super-class
            this._super = _super[name];
            
            // The method only need to be bound temporarily, so we
            // remove it when we're done executing
            var ret = fn.apply(this, arguments);        
            this._super = tmp;
            
            return ret;
          };
        })(name, prop[name]) :
        prop[name];
    }
    
    // The dummy class constructor
    function Class() {
      // All construction is actually done in the __init__ method
      if (!initializing && this.__init__)
        this.__init__.apply(this, arguments);
    }

    // Populate our constructed prototype object
    Class.prototype = prototype;

    // Enforce the constructor to be what we expect
    Class.constructor = Class;

    // And make this class extendable
    Class.extend = arguments.callee;
    
    return Class;
  };

  Oink.str = function (subject) {
    if (subject === null) {
      return 'null';
    } else if (subject === undefined) {
      return 'undefined';
    } else if (subject.__str__) {
      return subject.__str__();
    } else if (subject.__repr__) {
      return subject.__repr__();
    } else if (subject.length) {
      var str = '[';
      for (var i = 0; i < subject.length; ++i) {
        str += Oink.str(subject[i]);
        if (i < subject.length - 1) {
          str += ', ';
        }
      }
      str += ']';
      return str;
    } else {
      return subject;
    }
  }

  Oink.each = function (subject, callback) {
    if (subject.length) {
      for (var i = 0; i < subject.length; ++i) {
        callback(subject[i]);
      }
    } else {
      for (var i in subject) {
        callback(i, subject[i]);
      }
    }
  }

  Oink.range = function (start, end, stride) {
    var result = [];
    stride = stride || 1;
    if (stride > 0) {
      if (end === undefined) {
        for (var i = 0; i < start; i += stride) {
          result.push(i);
        }
      } else {
        for (var i = start; i < end; i += stride) {
          result.push(i);
        }
      }
    } else {
      for (var i = start; i > end; i += stride) {
        result.push(i);
      }
    }
    return result;
  }

  Oink.listComprehension = function(subject, value, test) {
    var result = [];
    Oink.each(subject, function () {
      if (test === undefined || test.apply(test, arguments)) {
        result.push(value.apply(value, arguments))
      }
    });
    return result;
  }

  Oink.sum = function (subject) {
    var sum = 0;
    Oink.each(subject, function (element) {
      sum += element;
    });
    return sum;
  }

  Oink.in_ = function (subject, element) {
    if (subject.length) {
      for (var i in subject) {
        if (subject[i] == value) {
          return true;
        }
      }
      return false;
    }
    return element in subject;
  }
})();
