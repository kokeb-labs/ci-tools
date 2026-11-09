// Seeded violation: GNU attribute and builtin, both compiler extensions.
#include <cstdint>

namespace kv::rule_4_1_1::bad {

__attribute__((noinline)) std::uint32_t twice(std::uint32_t v) { return v << 1U; }  // seeded

std::uint32_t pick(std::uint32_t v) {
  return __builtin_expect(v != 0U, 1) ? twice(v) : 0U;  // seeded
}

}  // namespace kv::rule_4_1_1::bad
