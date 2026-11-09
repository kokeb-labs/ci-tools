// Seeded violation: memory from new[] released with delete.
#include <cstdint>

namespace kv::rule_4_1_3_dealloc_mismatch::bad {

void release() {
  std::uint32_t* p = new std::uint32_t[4];
  delete p;  // array new, scalar delete
}

}  // namespace kv::rule_4_1_3_dealloc_mismatch::bad
