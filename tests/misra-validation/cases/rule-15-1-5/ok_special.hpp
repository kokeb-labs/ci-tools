// Near miss: only special members beside the initializer_list constructor.
#ifndef KV_RULE_15_1_5_OK_SPECIAL_HPP
#define KV_RULE_15_1_5_OK_SPECIAL_HPP

#include <cstddef>
#include <cstdint>
#include <initializer_list>

namespace kv::rule_15_1_5::ok_special {

class Samples {
 public:
  explicit Samples(std::initializer_list<std::uint16_t> values) : count_(values.size()) {}
  Samples(const Samples&) = default;
  Samples(Samples&&) noexcept = default;
  Samples& operator=(const Samples&) & = default;
  Samples& operator=(Samples&&) & noexcept = default;
  ~Samples() = default;

  [[nodiscard]] std::size_t count() const { return count_; }

 private:
  std::size_t count_;
};

}  // namespace kv::rule_15_1_5::ok_special

#endif  // KV_RULE_15_1_5_OK_SPECIAL_HPP
