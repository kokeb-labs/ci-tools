// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_6_7_2::bad_edge {

namespace {
std::int32_t g_hidden = 0;  // mutable, internal linkage, namespace scope
}  // namespace
inline std::int32_t g_level = 0;  // a mutable inline variable
std::int32_t touch() {
  g_hidden = 1;
  g_level = 2;
  return g_hidden + g_level;
}

}  // namespace kv::rule_6_7_2::bad_edge
