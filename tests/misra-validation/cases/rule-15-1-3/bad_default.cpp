// Seeded violation: a constructor callable with one argument through a default argument.
#include <cstdint>

namespace kv::rule_15_1_3::bad_default {

class Ratio {
 public:
  Ratio(std::int32_t num, std::int32_t den = 1) : num_(num), den_(den) {}

  [[nodiscard]] std::int32_t num() const { return num_; }
  [[nodiscard]] std::int32_t den() const { return den_; }

 private:
  std::int32_t num_;
  std::int32_t den_;
};

}  // namespace kv::rule_15_1_3::bad_default
