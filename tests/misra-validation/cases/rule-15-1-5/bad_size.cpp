// Seeded violation: an initializer_list constructor and a size constructor in one class.
#include <cstddef>
#include <cstdint>
#include <initializer_list>

namespace kv::rule_15_1_5::bad_size {

class Samples {
 public:
  Samples(std::initializer_list<std::uint16_t> values) : count_(values.size()) {}
  explicit Samples(std::size_t count) : count_(count) {}  // seeded

  [[nodiscard]] std::size_t count() const { return count_; }

 private:
  std::size_t count_;
};

}  // namespace kv::rule_15_1_5::bad_size
