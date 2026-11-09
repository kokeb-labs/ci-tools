// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_2_SHARED_PTR_UNIQUE_OK_NEAR_HPP
#define KV_RULE_4_1_2_SHARED_PTR_UNIQUE_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_4_1_2_shared_ptr_unique::near {

// A user class with a member named unique: not shared_ptr::unique.
class Handle {
 public:
  [[nodiscard]] bool unique() const { return owners_ == 1U; }

 private:
  std::uint32_t owners_{1U};
};

}  // namespace kv::rule_4_1_2_shared_ptr_unique::near

#endif  // KV_RULE_4_1_2_SHARED_PTR_UNIQUE_OK_NEAR_HPP
