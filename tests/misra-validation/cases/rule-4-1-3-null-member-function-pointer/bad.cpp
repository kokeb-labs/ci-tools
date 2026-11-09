// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_4_1_3_null_member_function_pointer::bad {

struct Motor {
  std::uint32_t speed() const { return 3U; }
};
std::uint32_t call_null(const Motor& m) {
  std::uint32_t (Motor::*fn)() const = nullptr;
  return (m.*fn)();  // null pointer to member function called  // seeded
}

}  // namespace kv::rule_4_1_3_null_member_function_pointer::bad
