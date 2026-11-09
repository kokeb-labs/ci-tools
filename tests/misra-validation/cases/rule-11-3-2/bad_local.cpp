// Seeded violation (local): a local object with three levels of pointer.
#include <cstdint>

namespace kv::rule_11_3_2::bad_local {

std::int32_t chase(std::int32_t** pp) {
  std::int32_t*** ppp = &pp;  // seeded
  return ***ppp;
}

}  // namespace kv::rule_11_3_2::bad_local
