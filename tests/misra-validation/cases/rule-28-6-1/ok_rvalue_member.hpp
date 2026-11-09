// Compliant near miss: std::move of a member in a non-const, rvalue-qualified member function.
#ifndef KV_RULE_28_6_1_OK_RVALUE_MEMBER_HPP
#define KV_RULE_28_6_1_OK_RVALUE_MEMBER_HPP

#include <array>
#include <cstdint>
#include <utility>

namespace kv::rule_28_6_1::ok_rvalue_member {

struct Buffer {
  std::array<std::uint8_t, 4U> data;
};

class Holder {
 public:
  [[nodiscard]] Buffer take() && { return std::move(buffer_); }

 private:
  Buffer buffer_{};
};

[[nodiscard]] inline Buffer drain() { return Holder{}.take(); }

}  // namespace kv::rule_28_6_1::ok_rvalue_member

#endif  // KV_RULE_28_6_1_OK_RVALUE_MEMBER_HPP
