// Seeded violation: declarator lists with initializers, for members and at namespace scope.
#include <cstdint>

namespace kv::rule_10_0_1_initialised::bad {

struct Span {
  std::int32_t lo = 0, hi = 8;
};

std::int32_t g_low = 1, g_high = 2;

std::int32_t width(const Span& s) { return (s.hi - s.lo) + (g_high - g_low); }

}  // namespace kv::rule_10_0_1_initialised::bad
