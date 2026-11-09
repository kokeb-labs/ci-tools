// Compliant: non-static data members are not variables for this rule, and these are used.
#ifndef KV_RULE_0_2_1_OK_MEMBER_HPP
#define KV_RULE_0_2_1_OK_MEMBER_HPP

#include <cstdint>

namespace kv::rule_0_2_1::ok_member {

template <typename Port>
class Driver {
 public:
  void Mark(std::uint8_t bit) noexcept {
    mask_ = static_cast<std::uint8_t>(static_cast<std::uint32_t>(mask_) | static_cast<std::uint32_t>(bit));
    seen_ = true;
  }
  [[nodiscard]] std::uint8_t Mask() const noexcept { return seen_ ? mask_ : std::uint8_t{0U}; }

 private:
  std::uint8_t mask_{0U};
  bool seen_{false};
};

inline std::uint8_t use() noexcept {
  Driver<int> d{};
  d.Mark(2U);
  return d.Mask();
}

}  // namespace kv::rule_0_2_1::ok_member

#endif  // KV_RULE_0_2_1_OK_MEMBER_HPP
