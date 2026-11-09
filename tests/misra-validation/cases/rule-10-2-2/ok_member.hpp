// Near miss: an unscoped enumeration declared as a class member, which the guideline's exception permits.
#ifndef KV_RULE_10_2_2_OK_MEMBER_HPP
#define KV_RULE_10_2_2_OK_MEMBER_HPP

#include <cstdint>

namespace kv::rule_10_2_2::ok_member {

class Port {
 public:
  enum Mode : std::int32_t { kInput, kOutput };

  [[nodiscard]] bool is_output() const { return mode_ == kOutput; }

 private:
  Mode mode_ = kInput;
};

}  // namespace kv::rule_10_2_2::ok_member

#endif  // KV_RULE_10_2_2_OK_MEMBER_HPP
