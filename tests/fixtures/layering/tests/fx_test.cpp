#include <vector>

#include "app/app.hpp"
#include "unit/check.hpp"

int main() {
  std::vector<int> v{1, 2};
  return CHECK(app::CountTo(3U) == 3U) + CHECK(v.size() == 2U);
}
