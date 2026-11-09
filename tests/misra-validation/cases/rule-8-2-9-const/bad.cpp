// Seeded violation: typeid applied to a const polymorphic object.
#include <typeinfo>

namespace kv::rule_8_2_9_const::bad {

struct Shape {
  virtual ~Shape() = default;
};

bool same_kind(const Shape& a, const Shape& b) {
  return typeid(a) == typeid(b);  // seeded
}

}  // namespace kv::rule_8_2_9_const::bad
