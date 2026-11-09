#ifndef KV_RULE_6_8_3_OK_HPP
#define KV_RULE_6_8_3_OK_HPP

// Compliant: only the address of an object that outlives the holder is stored.
#include <cstdint>

namespace kv::rule_6_8_3::ok {

class Holder {
 public:
  void attach(std::int32_t& longer_lived) { target_ = &longer_lived; }
  [[nodiscard]] bool attached() const { return target_ != nullptr; }

 private:
  std::int32_t* target_{nullptr};
};

}  // namespace kv::rule_6_8_3::ok

#endif  // KV_RULE_6_8_3_OK_HPP
