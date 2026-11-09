// Near miss: an empty base class need not be named in the initializer list (the guideline's exception).
#ifndef KV_RULE_15_1_2_OK_EMPTY_HPP
#define KV_RULE_15_1_2_OK_EMPTY_HPP

#include <cstdint>

namespace kv::rule_15_1_2::ok_empty {

struct Tag {};

class Tagged : public Tag {
 public:
  explicit Tagged(std::uint32_t v) : value_(v) {}

  [[nodiscard]] std::uint32_t value() const { return value_; }

 private:
  std::uint32_t value_;
};

}  // namespace kv::rule_15_1_2::ok_empty

#endif  // KV_RULE_15_1_2_OK_EMPTY_HPP
