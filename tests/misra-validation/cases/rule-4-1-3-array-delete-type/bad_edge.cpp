// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_4_1_3_array_delete_type::bad_edge {

struct Shape {
  virtual ~Shape() = default;
};
struct Square : Shape {
  std::uint32_t side{1U};
};
void drop(Shape* shapes) { delete[] shapes; }
void make_and_drop() { drop(new Square[3]); }

}  // namespace kv::rule_4_1_3_array_delete_type::bad_edge
