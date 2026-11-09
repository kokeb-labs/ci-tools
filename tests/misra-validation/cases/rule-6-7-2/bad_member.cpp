// Seeded violation (member): a mutable static data member is a global variable too.
#include <cstdint>

namespace kv::rule_6_7_2::bad_member {

struct Stats {
  static std::int32_t samples;
};

std::int32_t Stats::samples = 0;  // seeded

std::int32_t sampled() { return Stats::samples; }

}  // namespace kv::rule_6_7_2::bad_member
