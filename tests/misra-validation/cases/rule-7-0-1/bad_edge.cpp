// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_7_0_1::bad_edge {

inline std::int32_t take(std::int32_t v) { return v; }

std::int32_t accumulate(bool flag) {
  std::int32_t total = 10;
  total += flag;
  return total;
}

std::int32_t pass(bool flag) { return take(flag); }

std::int32_t as_number(bool flag) { return flag; }

template <typename T>
T plus_flag(T base, bool flag) {
  return base + flag;
}

std::int32_t use_template(bool flag) { return plus_flag<std::int32_t>(1, flag); }

}  // namespace kv::rule_7_0_1::bad_edge
