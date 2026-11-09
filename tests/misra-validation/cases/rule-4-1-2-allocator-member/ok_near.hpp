// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_2_ALLOCATOR_MEMBER_OK_NEAR_HPP
#define KV_RULE_4_1_2_ALLOCATOR_MEMBER_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_4_1_2_allocator_member::near {

// A user type whose member functions share the names of the removed allocator members.
class Pool {
 public:
  [[nodiscard]] std::uint32_t max_size() const { return 16U; }
  [[nodiscard]] const std::uint32_t* address(const std::uint32_t& x) const { return &x; }
};

}  // namespace kv::rule_4_1_2_allocator_member::near

#endif  // KV_RULE_4_1_2_ALLOCATOR_MEMBER_OK_NEAR_HPP
