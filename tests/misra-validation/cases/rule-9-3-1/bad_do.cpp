// Seeded violation (do): a do-while body and a nested for body without braces, plus an unbraced switch.
#include <cstdint>

namespace kv::rule_9_3_1::bad_do {

std::int32_t spin(std::int32_t n, std::int32_t mode) {
  std::int32_t total = 0;
  do
    ++total;
  while (total < n);
  for (std::int32_t i = 0; i < n; ++i) {
    for (std::int32_t j = 0; j < i; ++j)
      total += j;
  }
  switch (mode)
    case 2:
      total = 2;
  return total;
}

}  // namespace kv::rule_9_3_1::bad_do
