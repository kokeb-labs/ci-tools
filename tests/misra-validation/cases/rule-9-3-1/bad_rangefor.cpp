// Seeded violation (rangefor): a range-for body and a switch body that are single statements.
#include <array>
#include <cstdint>

namespace kv::rule_9_3_1::bad_rangefor {

std::int32_t sum(const std::array<std::int32_t, 3>& values, std::int32_t mode) {
  std::int32_t total = 0;
  for (const std::int32_t v : values)
    total += v;
  switch (mode)
    case 0:
      total = 0;
  return total;
}

}  // namespace kv::rule_9_3_1::bad_rangefor
