import pygame

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.state = 'initial'
        self.hit = False
        self.current_sprite = pygame.image.load('./assets/enemy.png')
        self.rect = self.current_sprite.get_rect()
        self.starting_position = (400, 100)
        self.rect.center = self.starting_position
        self.speed = 2  # Enemy speed
        self.extra_wait_if_hit = 1000  # Additional delay after being hit
        self.hit_time = 0
    def is_protected_by_wall(self, wall):
        # Calculate margins for horizontal alignment based on the sprite widths
        enemy_left = self.rect.left
        enemy_right = self.rect.right
        wall_left = wall.rect.left
        wall_right = wall.rect.right

        # Check if the enemy is horizontally within the boundaries of the wall
        is_horizontally_protected = wall_left <= enemy_left and enemy_right <= wall_right

        # Check if the enemy is just below the wall to be considered protected
        is_vertically_below = self.rect.y < wall.rect.y

        return is_horizontally_protected and is_vertically_below

    def move(self, direction):
        # Move the enemy in the specified direction
        self.rect.x += direction * self.speed

    def update(self, bullets, walls):
        current_time = pygame.time.get_ticks()
        min_distance_x = float('inf')  # Initialize min_distance_x before the loop

        # Find the closest bullet below the enemy
        closest_bullet = None
        for bullet in bullets:
            if bullet.rect.y > self.rect.y:  # Only consider bullets below
                distance_x = abs(bullet.rect.x - self.rect.x)
                if distance_x < min_distance_x:
                    min_distance_x = distance_x
                    closest_bullet = bullet

        if self.state == 'initial' and closest_bullet:
            # Change direction based on position of closest bullet
            self.state = 'move_right' if closest_bullet.rect.x < self.rect.x else 'move_left'

        elif self.state in ['move_left', 'move_right']:
            # Move the enemy and determine if it should go to 'waiting' or 'return'
            direction = 1 if closest_bullet and closest_bullet.rect.x < self.rect.x else -1
            self.move(direction)
            if any(self.is_protected_by_wall(w) for w in walls):
                if self.hit or  closest_bullet and  any(bullet.rect.y > self.rect.y for bullet in bullets):
                    self.state = 'waiting'
                else:
                    self.state = 'return'

        elif self.state == 'hiting':
            # If hit and not behind a wall, continue moving towards the nearest wall for cover
            direction = 1 if self.starting_position[0] < self.rect.x else -1
            self.move(direction)
            if any(self.is_protected_by_wall(w) for w in walls):
                self.state = 'waiting'
                self.hit_time = current_time

        elif self.state == 'waiting':
            # Stay in hiding if bullets are still coming
            if not closest_bullet or not any(bullet.rect.y > self.rect.y for bullet in bullets):
                if current_time - self.hit_time > self.extra_wait_if_hit:
                    self.state = 'return'

        elif self.state == 'return':
            # Return to initial position if possible
            if self.rect.centerx != self.starting_position[0]:
                direction = 1 if self.rect.centerx < self.starting_position[0] else -1
                self.move(direction)
            else:
                self.state = 'initial'
                if self.hit:
                    self.hit = False  # Reset after returning

        # Handle collision with bullets
        if pygame.sprite.spritecollide(self, bullets, dokill=True):
            if self.state != 'return':
                self.hit = True
                # Enter 'hiting' state if not already behind a wall, otherwise go to 'waiting'
                if not any(self.is_protected_by_wall(w) for w in walls):
                    self.state = 'hiting'
                else:
                    self.state = 'waiting'
                    self.hit_time = current_time
