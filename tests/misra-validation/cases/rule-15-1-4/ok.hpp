#ifndef KV_RULE_15_1_4_OK_HPP
#define KV_RULE_15_1_4_OK_HPP

// Compliant: every member is initialised, in the member initializer list or by a default member initializer.
#include <cstdint>

namespace kv::rule_15_1_4::ok {

class Channel {
 public:
  explicit Channel(std::uint8_t index) : index_(index) {}

  [[nodiscard]] std::uint8_t index() const { return index_; }
  [[nodiscard]] std::uint16_t gain() const { return gain_; }

 private:
  std::uint8_t index_;
  std::uint16_t gain_ = 1U;
};

}  // namespace kv::rule_15_1_4::ok

#endif  // KV_RULE_15_1_4_OK_HPP
