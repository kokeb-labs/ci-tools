// Seeded violation (decl): an if condition that declares an integer is converted to bool (unlike a while
// condition, the guideline gives no exception for it: if has an init-statement instead).
#include <cstdint>

namespace kv::rule_7_0_2::bad_decl {

std::int32_t next_value();

std::int32_t first_value() {
  if (std::int32_t v = next_value()) {  // seeded
    return v;
  }
  return 0;
}

}  // namespace kv::rule_7_0_2::bad_decl
