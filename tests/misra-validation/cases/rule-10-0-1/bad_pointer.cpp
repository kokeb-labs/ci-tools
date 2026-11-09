// Seeded violation (pointer): a pointer and an object in one local declaration, two namespace-scope objects in one.
#include <cstdint>

namespace kv::rule_10_0_1::bad_pointer {

std::int32_t g_low, g_high;

std::int32_t pick(std::int32_t v) {
  std::int32_t* p = nullptr, q = v;
  p = &q;
  return *p + g_low + g_high;
}

}  // namespace kv::rule_10_0_1::bad_pointer
