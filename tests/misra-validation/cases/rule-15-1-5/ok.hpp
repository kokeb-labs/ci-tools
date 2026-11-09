#ifndef KV_RULE_15_1_5_OK_HPP
#define KV_RULE_15_1_5_OK_HPP

// Compliant: the initializer_list constructor is the only constructor besides the special members.
#include <cstddef>
#include <cstdint>
#include <initializer_list>

namespace kv::rule_15_1_5::ok {

class Samples {
 public:
  explicit Samples(std::initializer_list<std::uint16_t> values) : count_(values.size()) {}

  [[nodiscard]] std::size_t count() const { return count_; }

 private:
  std::size_t count_;
};

}  // namespace kv::rule_15_1_5::ok

#endif  // KV_RULE_15_1_5_OK_HPP
