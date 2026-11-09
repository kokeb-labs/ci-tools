#ifndef KV_RULE_15_1_3_OK_HPP
#define KV_RULE_15_1_3_OK_HPP

// Compliant: the converting constructor and the conversion operator are both explicit.
#include <cstdint>

namespace kv::rule_15_1_3::ok {

class Millivolts {
 public:
  explicit Millivolts(std::int32_t mv) : mv_(mv) {}
  explicit operator std::int32_t() const { return mv_; }

 private:
  std::int32_t mv_;
};

}  // namespace kv::rule_15_1_3::ok

#endif  // KV_RULE_15_1_3_OK_HPP
