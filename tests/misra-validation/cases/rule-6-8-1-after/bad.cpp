// Seeded violation: a pointer to a block-scope object is read after the block has ended.
#include <cstdint>

namespace kv::rule_6_8_1_after::bad {

std::int32_t stale() {
  std::int32_t const* p = nullptr;
  {
    std::int32_t local = 7;
    p = &local;
  }
  return *p;  // seeded
}

}  // namespace kv::rule_6_8_1_after::bad
