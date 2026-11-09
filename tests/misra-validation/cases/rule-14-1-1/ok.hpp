#ifndef KV_RULE_14_1_1_OK_HPP
#define KV_RULE_14_1_1_OK_HPP

// Compliant: one type keeps every data member private, the other every member public.
#include <cstdint>

namespace kv::rule_14_1_1::ok {

class Reading {
 public:
  [[nodiscard]] std::int32_t raw() const { return raw_; }
  [[nodiscard]] std::int32_t scale() const { return scale_; }

 private:
  std::int32_t raw_ = 0;
  std::int32_t scale_ = 1;
};

struct Pair {
  std::int32_t first = 0;
  std::int32_t second = 0;
};

[[nodiscard]] inline bool same(const Pair& p) { return p.first == p.second; }

}  // namespace kv::rule_14_1_1::ok

#endif  // KV_RULE_14_1_1_OK_HPP
