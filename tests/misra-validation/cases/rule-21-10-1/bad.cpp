// Seeded violation: arguments read through the <cstdarg> facilities.
#include <cstdarg>
#include <cstdint>

namespace kv::rule_21_10_1::bad {

std::int32_t sum(std::int32_t count, ...) {
  std::va_list args;
  va_start(args, count);  // seeded: codeql
  std::int32_t total = 0;
  for (std::int32_t i = 0; i < count; ++i) {
    total += va_arg(args, std::int32_t);  // seeded
  }
  va_end(args);
  return total;
}

}  // namespace kv::rule_21_10_1::bad
