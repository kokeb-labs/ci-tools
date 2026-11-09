// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_5_7_3::bad_edge {

std::uint32_t three() {
  // the next line is part of this comment \
  return 4U;
  return 3U;
}

}  // namespace kv::rule_5_7_3::bad_edge
