// Seeded violation: a copy constructor that takes a non-const reference.
#include <cstdint>

namespace kv::rule_15_0_2::bad_ctor {

class Counter {
 public:
  Counter() = default;
  Counter(Counter& other) : count_(other.count_) {}  // seeded
  Counter(Counter&&) noexcept = default;
  Counter& operator=(const Counter&) & = default;
  Counter& operator=(Counter&&) & noexcept = default;
  ~Counter() = default;

 private:
  std::uint32_t count_ = 0U;
};

}  // namespace kv::rule_15_0_2::bad_ctor
