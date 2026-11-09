// Seeded violation (twocounters): two loop counters declared and stepped in one for statement.
#include <cstdint>

namespace kv::rule_9_5_1::bad_twocounters {

std::int32_t meet(std::int32_t n) {
  std::int32_t hits = 0;
  for (std::int32_t i = 0, j = n; i < j; ++i, --j) {
    ++hits;
  }
  return hits;
}

}  // namespace kv::rule_9_5_1::bad_twocounters
