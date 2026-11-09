// Edge cases of the seeded violation.
#include <typeinfo>

namespace kv::rule_8_2_9::bad_edge {

struct Shape {
  virtual ~Shape() = default;
};

bool is_shape(Shape const* p) { return typeid(*p) == typeid(Shape); }

}  // namespace kv::rule_8_2_9::bad_edge
