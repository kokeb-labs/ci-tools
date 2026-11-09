// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_6_4_3::bad_edge {

std::int32_t offset() { return 10; }
template <typename T>
struct Store {
  std::int32_t offset() const { return 20; }
};
template <typename T>
struct View : Store<T> {
  std::int32_t at() const { return offset(); }  // the global offset, not the dependent base's
};
std::int32_t use_view() { return View<std::int16_t>{}.at(); }

}  // namespace kv::rule_6_4_3::bad_edge
