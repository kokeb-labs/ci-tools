// Seeded violation: the results of remove, unique and empty thrown away.
#include <algorithm>
#include <array>
#include <cstdint>
#include <vector>

namespace kv::rule_28_6_4::bad {

void tidy(std::array<std::int32_t, 6U>& values) {
  std::remove(values.begin(), values.end(), 0);
  std::unique(values.begin(), values.end());
}

void check(const std::vector<std::int32_t>& values) { values.empty(); }

}  // namespace kv::rule_28_6_4::bad
