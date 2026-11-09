// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_4_1_3_dealloc_mismatch::bad_edge {

void scalar_new_array_delete() {
  std::uint32_t* p = new std::uint32_t(4U);
  delete[] p;  // scalar new, array delete
}

}  // namespace kv::rule_4_1_3_dealloc_mismatch::bad_edge
