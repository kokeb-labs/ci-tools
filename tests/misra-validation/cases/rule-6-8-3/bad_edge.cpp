// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_6_8_3::bad_edge {

const std::int32_t* g_last = nullptr;
void remember() {
  const std::int32_t local = 6;
  g_last = &local;  // a namespace-scope pointer keeps a local's address  // seeded
}

}  // namespace kv::rule_6_8_3::bad_edge
