// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_2_ALLOCATOR_VOID_OK_NEAR_HPP
#define KV_RULE_4_1_2_ALLOCATOR_VOID_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_4_1_2_allocator_void::near {

// A user template named allocator, specialised for void: not std::allocator<void>.
template <typename T>
struct allocator {
  std::uint32_t id{0U};
};
using VoidTag = allocator<void>;
inline std::uint32_t id_of(const VoidTag& t) { return t.id; }

}  // namespace kv::rule_4_1_2_allocator_void::near

#endif  // KV_RULE_4_1_2_ALLOCATOR_VOID_OK_NEAR_HPP
