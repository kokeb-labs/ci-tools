// Edge cases of the seeded violation.
#include <typeinfo>

namespace kv::rule_8_2_9_codeql::bad_edge {

struct Shape {
  virtual ~Shape() = default;
};

bool is_shape(Shape* p) { return typeid(*p) == typeid(Shape); }  // seeded

}  // namespace kv::rule_8_2_9_codeql::bad_edge
