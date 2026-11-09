// Seeded violation: a mutable namespace-scope variable and a mutable static data member.
#include <cstdint>

namespace kv::rule_6_7_2::bad {

std::int32_t g_errors = 0;

struct Stats {
  static std::int32_t samples;
};

std::int32_t Stats::samples = 0;

std::int32_t bump() {
  ++g_errors;
  return g_errors + Stats::samples;
}

}  // namespace kv::rule_6_7_2::bad
