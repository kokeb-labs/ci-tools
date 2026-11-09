// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_6_7_2::bad_edge {

namespace {
std::int32_t g_hidden = 0;  // seeded
}  // namespace
inline std::int32_t g_level = 0;  // seeded
std::int32_t read_seed();
const std::int32_t kSeed = read_seed();  // seeded
std::int32_t touch() {
  g_hidden = 1;
  g_level = 2;
  return g_hidden + g_level + kSeed;
}

}  // namespace kv::rule_6_7_2::bad_edge
