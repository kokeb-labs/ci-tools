// Seeded violation: null pointers spelled as NULL and as a literal zero.
#include <cstddef>
#include <cstdint>

namespace kv::rule_7_11_1::bad {

bool missing(std::int32_t const* p) {
  std::int32_t const* none = NULL;  // seeded
  std::int32_t const* zero = 0;  // seeded
  return (p == none) || (p == zero);
}

}  // namespace kv::rule_7_11_1::bad
