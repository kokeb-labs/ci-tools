// Seeded violation: a va_list copied with va_copy and handed to a helper.
#include <cstdarg>
#include <cstdint>

namespace kv::rule_21_10_1::bad_copy {

std::int32_t first_of(std::va_list args) { return va_arg(args, std::int32_t); }  // seeded

std::int32_t peek(std::int32_t count, ...) {
  std::va_list args;
  va_start(args, count);
  std::va_list again;
  va_copy(again, args);  // seeded: codeql
  const std::int32_t value = first_of(again);
  va_end(again);
  va_end(args);
  return value;
}

}  // namespace kv::rule_21_10_1::bad_copy
