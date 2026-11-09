// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_7_0_1::bad_edge {

inline std::int32_t take(std::int32_t v) { return v; }

std::int32_t accumulate(bool flag) {
  std::int32_t total = 10;
  total += flag;  // seeded
  return total;
}

std::int32_t pass(bool flag) { return take(flag); }  // seeded

std::int32_t as_number(bool flag) { return flag; }  // seeded

template <typename T>
T plus_flag(T base, bool flag) {
  return base + flag;  // seeded
}

std::int32_t use_template(bool flag) { return plus_flag<std::int32_t>(1, flag); }

bool both_bits(bool a, bool b) { return (a & b) != 0; }  // seeded

std::int32_t cast_flag(bool flag) { return static_cast<std::int32_t>(flag); }  // seeded

}  // namespace kv::rule_7_0_1::bad_edge
