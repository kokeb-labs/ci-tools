// Seeded violation: typeid applied to a polymorphic object.
#include <typeinfo>

namespace kv::rule_8_2_9_codeql::bad {

struct Shape {
  virtual ~Shape() = default;
};

bool same_kind(Shape& a, Shape& b) {
  return typeid(a) == typeid(b);  // seeded
}

}  // namespace kv::rule_8_2_9_codeql::bad
