# Oink - a Python to Javascript translator

Oink attempts to translate Python source to idiomatic Javascript.

It consists of the translator itself and a JS runtime.

## Examples

Here are a couple of examples from [Project Euler](http://projecteuler.net/):

### Project Euler 1

Python source for solution 1:

```python
def euler1():
    """Add all the natural numbers below 1000 that are multiples of 3 or 5"""
    multiple = lambda x, y: x % y == 0
    return sum(x for x in xrange(1, 1000)
               if multiple(x, 3) or multiple(x, 5))

print euler1()
```

Running `oink euler1.py` on this example produces the following Javascript:

```javascript
/** Add all the natural numbers below 1000 that are multiples of 3 or 5 */
function euler1() {
  var multiple = function (x, y) { return x % y == 0; };
  return Oink.sum(Oink.listComprehension(Oink.range(1, 1000), function (x) {
    return x;
  }, function (x) {
    return multiple(x, 3) || multiple(x, 5);
  }));
};

console.log(euler1());
```

### Project Euler 6

Python source for solution 6:

```python
def euler6(op, end):
    return op(sum(xrange(end + 1))) - sum(op(x) for x in xrange(end + 1))

print euler6(lambda x: x ** 2, 100)
```

Running `oink euler6.py` on this example produces the following Javascript:

```javascript
function euler6(op, end) {
  return op(Oink.sum(Oink.range(end + 1))) - Oink.sum(Oink.listComprehension(Oink.range(end + 1), function (x) {
      return op(x);
  }));
};

console.log(euler6(function (x) { return Math.pow(x, 2); }, 100));
```