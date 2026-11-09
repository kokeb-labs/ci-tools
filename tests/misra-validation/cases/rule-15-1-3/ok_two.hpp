// Near miss: two required parameters, and the implicit copy and move.
#ifndef KV_RULE_15_1_3_OK_TWO_HPP
#define KV_RULE_15_1_3_OK_TWO_HPP

#include <cstdint>

namespace kv::rule_15_1_3::ok_two {

class Ratio {
 public:
  Ratio(std::int32_t num, std::int32_t den) : num_(num), den_(den) {}
  Ratio(const Ratio&) = default;
  Ratio(Ratio&&) noexcept = default;
  Ratio& operator=(const Ratio&) & = default;
  Ratio& operator=(Ratio&&) & noexcept = default;
  ~Ratio() = default;

  [[nodiscard]] std::int32_t num() const { return num_; }
  [[nodiscard]] std::int32_t den() const { return den_; }

 private:
  std::int32_t num_;
  std::int32_t den_;
};

}  // namespace kv::rule_15_1_3::ok_two

#endif  // KV_RULE_15_1_3_OK_TWO_HPP
