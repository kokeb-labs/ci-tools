// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_8_14_1::bad_edge {

struct Log {
  std::uint32_t lines{0U};
};

bool record(Log& log) {
  log.lines = 1U;
  return true;
}

bool or_set(Log& log, bool fast) { return fast || ((log.lines = 2U) == 2U); }  // seeded

bool and_call(Log& log, bool on) { return on && record(log); }  // seeded

bool and_volatile(std::uint32_t volatile& reg, bool on) { return on && (reg == 1U); }  // seeded

}  // namespace kv::rule_8_14_1::bad_edge
