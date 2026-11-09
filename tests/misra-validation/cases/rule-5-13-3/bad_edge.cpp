// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_5_13_3::bad_edge {

std::uint32_t pick(std::uint32_t v) {
  std::uint32_t out = 0U;
  switch (v) {
    case 010U:  // octal eight in a case label
      out = 1U;
      break;
    default:
      out = 07U;  // a single-digit octal literal
      break;
  }
  return out;
}

}  // namespace kv::rule_5_13_3::bad_edge
